from wrangler import dw
import sys

if(len(sys.argv) < 3):
    sys.exit('Error: Please include an input and output file.  Example python script.py input.csv output.csv')

w = dw.DataWrangler()

# Split data repeatedly on newline  into  rows
w.add(dw.Split(column=["data"],
               table=0,
               status="active",
               drop=True,
               result="row",
               update=False,
               insert_position="right",
               row=None,
               on="\n",
               before=None,
               after=None,
               ignore_between=None,
               which=1,
               max=0,
               positions=None,
               quote_character=None))

# Fold   using  1 as a key
w.add(dw.Fold(column=[],
              table=0,
              status="active",
              drop=False,
              keys=[0]))

# Delete  every 7 rows 
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowCycle(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  cycle=7,
                  start=0,
                  end=None)])))

# Extract from value between ' any lowercase word |' and '}'
w.add(dw.Extract(column=["value"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on=".*",
                 before="}",
                 after="[a-z]+\\|",
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Fill extract  with values from above
w.add(dw.Fill(column=["extract"],
              table=0,
              status="active",
              drop=False,
              direction="down",
              method="copy",
              row=None))

# Delete  every 6 rows  starting with 6
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowCycle(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  cycle=6,
                  start=5,
                  end=None)])))

# Delete  every 5 rows 
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowCycle(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  cycle=5,
                  start=0,
                  end=None)])))

# Extract from fold on 'Titles'
w.add(dw.Extract(column=["fold"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="Titles",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from fold on 'Runners-up'
w.add(dw.Extract(column=["fold"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="Runners-up",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from fold on 'Third place'
w.add(dw.Extract(column=["fold"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="Third place",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from fold on 'Fourth place'
w.add(dw.Extract(column=["fold"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="Fourth place",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Drop fold
w.add(dw.Drop(column=["fold"],
              table=0,
              status="active",
              drop=True))

# Copy extract1
w.add(dw.Copy(column=["extract1"],
              table=0,
              status="active",
              drop=False,
              result="column",
              update=False,
              insert_position="right",
              row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowIndex(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  indices=[0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96])])))

# Drop extract1
w.add(dw.Drop(column=["extract1"],
              table=0,
              status="active",
              drop=True))

# Copy extract2
w.add(dw.Copy(column=["extract2"],
              table=0,
              status="active",
              drop=False,
              result="column",
              update=False,
              insert_position="right",
              row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowIndex(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  indices=[0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96])])))

# Copy extract3
w.add(dw.Copy(column=["extract3"],
              table=0,
              status="active",
              drop=False,
              result="column",
              update=False,
              insert_position="right",
              row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowIndex(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  indices=[0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96])])))

# Copy extract4
w.add(dw.Copy(column=["extract4"],
              table=0,
              status="active",
              drop=False,
              result="column",
              update=False,
              insert_position="right",
              row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowIndex(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  indices=[0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96])])))

# Drop extract4
w.add(dw.Drop(column=["extract4"],
              table=0,
              status="active",
              drop=True))

# Drop extract3
w.add(dw.Drop(column=["extract3"],
              table=0,
              status="active",
              drop=True))

# Drop extract2
w.add(dw.Drop(column=["extract2"],
              table=0,
              status="active",
              drop=True))

# Translate copy1 down
w.add(dw.Translate(column=["copy1"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values=1))

# Drop copy1
w.add(dw.Drop(column=["copy1"],
              table=0,
              status="active",
              drop=True))

# Translate copy2 down
w.add(dw.Translate(column=["copy2"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values=1))

# Translate translate1 down
w.add(dw.Translate(column=["translate1"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values=1))

# Drop translate1
w.add(dw.Drop(column=["translate1"],
              table=0,
              status="active",
              drop=True))

# Drop copy2
w.add(dw.Drop(column=["copy2"],
              table=0,
              status="active",
              drop=True))

# Translate copy3 down
w.add(dw.Translate(column=["copy3"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values="3"))

# Translate translate3 down
w.add(dw.Translate(column=["translate3"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values="3"))

# Translate translate4 down
w.add(dw.Translate(column=["translate4"],
                   table=0,
                   status="active",
                   drop=False,
                   direction="down",
                   values=1))

# Drop translate4, copy3, translate3
w.add(dw.Drop(column=["translate4","copy3","translate3"],
              table=0,
              status="active",
              drop=True))

# Merge translate, copy  with glue  
w.add(dw.Merge(column=["translate","copy"],
               table=0,
               status="active",
               drop=False,
               result="column",
               update=False,
               insert_position="right",
               row=None,
               glue=""))

# Drop copy, translate
w.add(dw.Drop(column=["copy","translate"],
              table=0,
              status="active",
              drop=True))

# Merge translate2, merge  with glue  
w.add(dw.Merge(column=["translate2","merge"],
               table=0,
               status="active",
               drop=False,
               result="column",
               update=False,
               insert_position="right",
               row=None,
               glue=""))

# Drop translate2, merge
w.add(dw.Drop(column=["translate2","merge"],
              table=0,
              status="active",
              drop=True))

# Merge merge1, translate5  with glue  
w.add(dw.Merge(column=["merge1","translate5"],
               table=0,
               status="active",
               drop=False,
               result="column",
               update=False,
               insert_position="right",
               row=None,
               glue=""))

# Drop merge1, translate5
w.add(dw.Drop(column=["merge1","translate5"],
              table=0,
              status="active",
              drop=True))

# Cut from value before ' (\['
w.add(dw.Cut(column=["value"],
             table=0,
             status="active",
             drop=False,
             result="column",
             update=True,
             insert_position="right",
             row=None,
             on=".*",
             before=" \\(\\[",
             after=None,
             ignore_between=None,
             which=1,
             max=1,
             positions=None))

# Split value repeatedly on ','
w.add(dw.Split(column=["value"],
               table=0,
               status="active",
               drop=True,
               result="column",
               update=False,
               insert_position="right",
               row=None,
               on=",",
               before=None,
               after=None,
               ignore_between=None,
               which=1,
               max="0",
               positions=None,
               quote_character=None))

# Extract from split on ' any number '
w.add(dw.Extract(column=["split"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="\\d+",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from split1 on ' any number  '
w.add(dw.Extract(column=["split1"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="\\d+ ",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from split2 on ' any number '
w.add(dw.Extract(column=["split2"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="\\d+",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from split3 on ' any number '
w.add(dw.Extract(column=["split3"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="\\d+",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Extract from split4 on ' any number '
w.add(dw.Extract(column=["split4"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on="\\d+",
                 before=None,
                 after=None,
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Drop split4, split3, split2, split1...
w.add(dw.Drop(column=["split4","split3","split2","split1","split"],
              table=0,
              status="active",
              drop=True))

# Fold extract5, extract6, extract7, extract8...  using  header as a key
w.add(dw.Fold(column=["extract5","extract6","extract7","extract8","extract9"],
              table=0,
              status="active",
              drop=False,
              keys=[-1]))

# Drop fold
w.add(dw.Drop(column=["fold"],
              table=0,
              status="active",
              drop=True))

# Delete  rows where value is null
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.IsNull(column=[],
                table=0,
                status="active",
                drop=False,
                lcol="value",
                value=None,
                op_str="is null")])))

w.apply_to_file(sys.argv[1]).print_csv(sys.argv[2])
