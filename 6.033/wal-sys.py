#!/usr/bin/python

import sys
import re
import os
import signal

redoMode = 1
undoMode = 2
mode = 1
LOG = None
DB = None

tid_stat = {} # Already assigned tids
current_db = {} # The in-memory database
on_disk_db = {} # The on-disk DB

winners = {}
losers = set()
done = set()

pending_writes = []

COMMITING = 1 # Pending
ENDING = 2 # Commited
DONE = 3 # DONE

START = 1
UPDATE = 2
ENDED = 3
OUTCOME = 4
CHECKPOINT = 5

def get_log_type(type_str):
    if type_str == 'START':
        return START
    elif type_str == 'UPDATE':
        return UPDATE
    elif type_str == 'END':
        return ENDED
    elif type_str == 'OUTCOME':
        return OUTCOME
    elif type_str == 'CHECKPOINT':
        return CHECKPOINT
    else:
        return 0

def get_tid_stat(tid):
    if tid_stat.has_key(tid):
        if tid_stat[tid] == COMMITING:
            return 'PENDING(WAITING COMMIT/ABORT)'
        elif tid_stat[tid] == ENDING:
            return 'COMMITTING (WAITING END)'
        else:
            return 'DONE'
    else:
        return 'NOT INITIALIZED'

def is_valid_command(tid, type, anum, value):
    if type == 'new':
        # new -> tid not in tid list
        if tid_stat.has_key(tid):
            print 'NEW tid: %s already exists' % tid
            return False
        else:
            return True
    elif type == 'init':
        if tid_stat.has_key(tid) and tid_stat[tid] == COMMITING:
            # complain if the value is already in the database
            if current_db.has_key(anum):
                print 'Cannot initialize %s to %s = already exists with value %s' % (anum, value, current_db[anum])
                return False
            else:
                return True
        else:
            print 'INIT tid: %s is in %s mode' % (tid, get_tid_stat(tid))
            return False
    elif type == 'write' or type == 'credit' or type == 'debit':
        if tid_stat.has_key(tid) and tid_stat[tid] == COMMITING:
            # Complain if the value is not in the database
            if current_db.has_key(anum):
                return True
            else:
                print 'Cannot update %s - not initialized' % anum
                return False
        else:
            print 'WRITE/DEBIT/CREDIT tid: %s is in %s mode' % (tid, get_tid_stat(tid))
            return False
    elif type == 'commit':
        if tid_stat.has_key(tid) and tid_stat[tid] == COMMITING:
            return True
        else:
            print 'COMMIT tid: %s is in %s mode' % (tid, get_tid_stat(tid))
            return False
    elif type == 'abort':
        if tid_stat.has_key(tid) and tid_stat[tid] == COMMITING:
            return True
        else:
            print 'ABORT tid: %s is in %s mode' % (tid, get_tid_stat(tid))
            return False
    elif type == 'end':
        if tid_stat.has_key(tid) and tid_stat[tid] == ENDING:
            return True
        else:
            print 'END tid: %s is in %s mode' % (tid, get_tid_stat(tid))
    else:
        return True
                                                   
def do_command(tid, type, anum, value):
    if type == 'begin':
        handle_begin(tid, type, anum, value)
    elif type == 'init':
        handle_init(tid, type, anum, int(value))
    elif type == 'write':
        handle_write(tid, type, anum, int(value))
    elif type == 'debit':
        handle_debit(tid, type, anum, int(value))
    elif type == 'credit':
        handle_credit(tid, type, anum, int(value))
    elif type == 'commit':
        handle_commit(tid, type, anum, value)
    elif type == 'end':
        handle_end(tid, type, anum, value)
    elif type == 'abort':
        handle_abort(tid, type, anum, value)
    else:
        print 'Command %s not yet implemented' % type

def handle_begin(tid, type, anum, value):
    tid_stat[tid] = COMMITING
    # Write a START record to log
    print 'Beginning id: %s' % tid
    LOG.write('type: START action_id: %s\n' % tid)

def handle_init(tid, type, anum, value):
    # Write an UPDATE record with old value = NULL
    print 'Initializing account %s to %s' % (anum, value)
    LOG.write('type: UPDATE action_id: %s variable: %s redo: "%s" undo: NULL\n' % (tid, anum, value))
    # set the value in db
    current_db[anum] = value
    write_to_disk(tid, anum, value)

def handle_write(tid, type, anum, value):
    # Write an UPDATE record
    oldvalue = current_db[anum]
    print 'Setting account %s to %s' % (anum, value)
    LOG.write('type: UPDATE action_id: %s variable: %s redo: "%s" undo: "%s"\n' % (tid, anum, value, oldvalue))
    current_db[anum] = value
    write_to_disk(tid, anum, value)

def handle_debit(tid, type, anum, value):
    # Write an UPDATE record
    oldvalue = current_db[anum]
    print 'Debiting account %s by %s' % (anum, value)
    value = oldvalue-value
    LOG.write('type: UPDATE action_id: %s variable: %s redo: "%s" undo: "%s"\n' % (tid, anum, value, oldvalue))
    current_db[anum] = value
    write_to_disk(tid, anum, value)

def handle_credit(tid, type, anum, value):
    # Write an UPDATE record
    oldvalue = current_db[anum]
    print 'Crediting account %s by %s' % (anum, value)
    value = oldvalue+value
    LOG.write('type: UPDATE action_id: %s variable: %s redo: "%s" undo: "%s"\n' % (tid, anum, value, oldvalue))
    current_db[anum] = value
    write_to_disk(tid, anum, value)

def handle_commit(tid, type, anum, value):
    # write an OUTCOME record with COMMITTED
    print 'Committing id: %s' % tid
    LOG.write('type: OUTCOME action_id: %s status: COMMITTED\n' % tid)
    tid_stat[tid] = ENDING

def handle_abort(tid, type, anum, value):
    # Undo all the actions of this tid
    print 'Aborting id: %s' % tid
    undo_tid(tid)
    # Write an OUTCOME record with ABORTED
    LOG.write('type: OUTCOME action_id: %s status: ABORTED\n' % tid)
    tid_stat[tid] = ENDING

def handle_end(tid, type, anum, value):
    # Flush all the records to disk
    print 'Ending id: %s' % tid
    flush_updates(tid)
    # Write an END record
    LOG.write('type: END action_id: %s\n' % tid)
    tid_stat[tid] = DONE

def write_to_disk(tid, anum, value, delete=False):
    if mode == undoMode:
        forced_write_to_disk(tid, anum, value, delete)
    else:
        # Add to the pending writes
        pending_writes.append((tid, anum, value, delete))

def forced_write_to_disk(tid, anum, value, delete):
    if delete:
        del on_disk_db[anum]
    else:
        on_disk_db[anum] = value

def flush_updates(tid):
    for (pending_tid, anum, value, delete) in pending_writes:
        if pending_tid == tid:
            forced_write_to_disk(pending_tid, anum, value, delete)

# Undo a tid
# Read the whole log (from start) and find all the writes corresponding to this tid and add them to a table
# starting from the last one do all the undo to the in_memory_db and use write_to_disk
def undo_tid(tid):
    global LOG
    updates = []
    #reset the LOG to start
    close(LOG)
    try:
        LOG = open('LOG', 'r')
    except IOError:
        exit('Could not open LOG for reading')
    line = LOG.readline()
    while line:
        fields = re.split(r'\s+', line)
        if fields[3] == tild and fields[1] == 'UPDATE':
            match = re.match(r'\"(\S+)\"', fields[9])
            if match:
                updates.append((tid, fields[5], match.group(1), False))
            else:
                updates.append((tid, fields[5], 0, True))
        line = LOG.readline()
    LOG.close()
    try:
        LOG = open('LOG', 'a')
    except IOError:
        exit('Could not open LOG for writing')
    # Undo the actions
    updates.reverse()
    for (tid, anum, value, delete) in updates:
        if delete:
            del current_db[anum]
        else:
            current_db[anum] = value
        write_to_disk(tid, anum, value, delete)

def process_command_input():
    global LOG
    command = None
    try:
        LOG = open('LOG', 'a')
    except IOError:
        sys.exit('Could not open LOG for writing')
    line = raw_input('> ')
    while line:
        matched = False
        finished = False
        match = re.match(r'begin\s+(\d+)\s*$', line)
        if match:
            matched = True
            command = (match.group(1), 'begin', 0, 0)
        if not matched:
            match = re.match(r'create_account\s+(\d+)\s+(\S+)\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'init', match.group(2), match.group(3))
        if not matched:
            match = re.match(r'write\s+(\d+)\s+(\S+)\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'write', match.group(2), match.group(3))
        if not matched:
            match = re.match(r'debit_account\s+(\d+)\s+(\S+)\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'debit', match.group(2), match.group(3))
        if not matched:
            match = re.match(r'credit_account\s+(\d+)\s+(\S+)\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'credit', match.group(2), match.group(3))
        if not matched:
            match = re.match(r'commit\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'commit', 0, 0)
        if not matched:
            match = re.match(r'abort\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'abort', 0, 0)
        if not matched:
            match = re.match(r'end\s+(\d+)\s*$', line)
            if match:
                matched = True
                command = (match.group(1), 'end', 0, 0)
        if not matched and re.match(r'show_state', line):
            matched = True
            finished = True
            print_db()
        if not matched and re.match(r'crash', line):
            matched = True
            finished = True
            do_crash()
        if not matched and re.match(r'checkpoint', line):
            matched = True
            finished = True
            do_checkpoint()
        if not matched:
            print 'invalid command: %s' % line
        elif not finished:
            (tid, type, anum, value) = command
            if is_valid_command(tid, type, anum, value):
                do_command(tid, type, anum, value)
            else:
                print 'An invalid command'
        line = raw_input('> ')
    do_crash()

def undo_update(name, new_val, old_val):
    match = re.match(r'\"(\S+)\"', old_val)
    if match:
        # do not dleete
        on_disk_db[name] = match.group(1)
    else:
        del on_disk_db[name]

def do_crash():
    print 'crashing ...'
    LOG.close()
    # dump the db to disk
    try:
        DB = open('DB', 'w')
    except IOError:
        sys.exit('Could not open DB for writing')
    for key in on_disk_db:
        DB.write('%s %s\n' % (key, on_disk_db[key]))
    DB.close()
    sys.exit(0)

def recover():
    global LOG
    # Read the log
    print 'Recovering the database ..'
    try:
        LOG = open('LOG', 'r')
    except IOError:
        sys.exit('Could not open LOG for reading')
    recovery_log = []
    line = LOG.readline()
    while line:
        # Split will return an empty string at the end if we don't take it off here
        fields = re.split(r'\s+', line)[:-1]
        recovery_log.append(fields)
        line = LOG.readline()
    LOG.close()
    # read the DB to current_db
    try:
        DB = open('DB', 'r')
    except IOError:
        sys.exit('Could not open DB for reading')
    line = DB.readline()
    while line:
        keyval = re.split(r'\s+', line)
        key = keyval[0]
        val = keyval[1]
        on_disk_db[key] = val
        line = DB.readline()
    DB.close()
    roll_back(recovery_log)
    if mode != undoMode:
        forward_scan(recovery_log)
    else:
        print ' Logging STATUS records for losers'
        try:
            LOG = open('LOG', 'a')
        except IOError:
            sys.exit('Could not open LOG for writing')
        for id in losers:
            LOG.write('type: OUTCOME action_id: %s status ABORTED\n' % id)
        LOG.close()
    current_db = on_disk_db.copy()
    print 'Recovery done'

def forward_scan(recovery_log):
    global LOG
    # We start the forward scane from the beginning of the log, in practice
    # we would start fomr last point of the roll back
    print 'Starting forward scan ...'
    for entry in recovery_log:
        type = get_log_type(entry[1])
        if type == 0:
            continue
        if type == UPDATE and winners.has_key(entry[3]) and winners[entry[3]] == 'COMMITTED':
            match = re.match(r'\"(\S+)\"', entry[7])
            if match:
                on_disk_db[entry[5]] = match.group(1)
                print '  REDOING: %s' % ' '.join(entry)
    try:
        LOG = open('LOG', 'a')
    except IOError:
        sys.exit('Could not open LOG for writing')
    print '  Logging END records for winners'
    for id in winners:
        LOG.write('type: END action_id: %s\n' % id)
    LOG.close()
    print 'Forward scan done'

    
def roll_back(recovery_log):
    global winners, losers, done
    pending_winners = set()
    pending_losers = set()
    reverselog = recovery_log[:]
    reverselog.reverse()
    tid = None

    done_cp = False
    winners = {}
    losers = set()
    done = set()
    line_c = 0
    print 'Starting rollback ...'
    for entry in reverselog:
        type = get_log_type(entry[1])
        if type == 0:
            continue
        line_c+=1
        if type != CHECKPOINT:
            tid = entry[3]
        if type == CHECKPOINT:
            # Search for PENDING Entries
            i = 3
            while i < len(entry):
                if entry[i] == 'COMMITTED:':
                    i+=1
                    break
                # When we find a loser
                if entry[i] == 'id:':
                    i+=1
                    continue
                if not winners.has_key(entry[i]) and not entry[i] in done:
                    losers.add(entry[i])
                    pending_losers.add(entry[i])
                i+=1
            # Seach for COMMITTED Entries
            while i < len(entry):
                if entry[i] == 'DONE:':
                    i+=1
                    break
                if entry[i] == 'id:':
                    i+=1
                    continue
                # Found a winner
                if not entry[i] in done:
                    winners[entry[i]] = EMPTY
                    pending_winners.add(entry[i])
                i+=1
            # Finally, search for DONE entries
            while i < len(entry):
                if entry[i] == 'id:':
                    i+=1
                    continue
                done.add(entry[i])
                i+=1
            done_cp = True
        elif done_cp:
            # when pending_winners and pending_losers are empty - we are done
            if (len(pending_winners) == 0 and mode == redoMode) or (len(pending_losers) == 0 and mode == undoMode):
                line_c-=1
                break

            if type == OUTCOME and winners.has_key(tid):
                winners[tid] = entry[5]
            
            if type == START:
                if tid in pending_winners:
                    pending_winners.remove(tid)
                if tid in pending_losers:
                    pending_losers.remove(tid)
            elif type == UPDATE:
                if tid in losers:
                    if mode != redoMode:
                        print '  UNDOING: %s' % ' '.join(entry)
                        undo_update(entry[5], entry[7], entry[9])
        else:
            # Haven't found a checkpoint yet
            if type == ENDED:
                done.add(tid)
            if type == OUTCOME and not tid in done:
                if tid not in losers:
                    winners[tid] = entry[5]
                    pending_winners.add(tid)
            if not tid in winners and not tid in done:
                if not tid in losers:
                    losers.add(tid)
                    pending_losers.add(tid)
                if type == UPDATE:
                    if mode != redoMode:
                        print '  UNDOING: %s' % ' '.join(entry)
                        undo_update(entry[5], entry[7], entry[9])
            if type == START:
                if tid in pending_losers:
                    pending_losers.remove(tid)
                if tid in pending_winners:
                    pending_winners.remove(tid)
    print '  The log was rolled back %s lines' % line_c

    print 'Rollback done'
    print 'Winners: %s ' % ' '.join(['id: %s' % x for x in winners]),
    print 'Losers: %s ' % ' '.join(['id: %s' % x for x in losers]),
    print 'Done: %s ' % ' '.join(['id: %s' % x for x in done])

                
            
    

def do_checkpoint():
    current_winners = []
    current_losers = []
    current_done = []

    print 'Doing checkpoint'

    for key in tid_stat:
        val = tid_stat[key]
        if val == COMMITING:
            current_losers.append(key)
        elif val == ENDING:
            current_winners.append(key)
        elif val == DONE:
            current_done.append(key)
    # Log the checkpoint
    LOG.write('type: CHECKPOINT ')
    LOG.write('PENDING: %s ' % ' '.join(['id: %s' % x for x in current_losers]))
    LOG.write('COMMITTED: %s ' % ' '.join(['id: %s' % x for x in current_winners]))
    LOG.write('DONE: %s \n' % ' '.join(['id: %s' % x for x in current_done]))
    
    

def usage():
    print 'usage : trans [-reset] [-redo|-undo]'

def print_db():
    dump_db()
    dump_log()

def dump_log():
    global LOG
    LOG.close()
    try:
        LOG = open('LOG', 'r')
        contents = LOG.read()
        print '\n-----------------------'
        print 'LOG contents:'
        print contents,
        print '-----------------------'
        LOG.close()
    except IOError:
        sys.exit('Could not open LOG for reading')
    try: 
        LOG = open('LOG', 'a')
    except IOError:
        sys.exit('Could not open LOG for writing')
        

def dump_db():
    print '\n-----------------------'
    print 'On-disk DB contents:'
    for key in on_disk_db:
        val = on_disk_db[key]
        print 'Account: %s Value: %s' % (key, val)
    print '-----------------------'


if __name__ == '__main__':
    for arg in sys.argv:
        if arg == 'python' or arg == 'wal-sys.py' or arg == './wal-sys.py':
            continue
        if arg == '-reset':
            os.system('rm -f LOG DB')
        elif arg == '-redo':
            mode = redoMode
        elif arg == '-undo':
            mode = undoMode
        else:
            usage()
            exit(0)
    try:
        LOG = open('LOG')
        LOG.close()
        recover()
    except IOError:
        print 'Opening new log'

    signal.signal(signal.SIGINT, lambda signum, frame : do_crash())
    process_command_input()

