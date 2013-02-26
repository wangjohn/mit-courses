#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <assert.h>
#include <pthread.h>
#include <assert.h>

#define NBUCKET 5          // Number of buckets in hash table
#define NENTRY 1000000     // Number of possible entries per bucket
#define NKEYS 100000       // Number of keys to insert and look up

// An entry in the hash table:
struct entry {
  int key;            // the key
  int value;          // the value
  int inuse;          // is entry in use?
};
// Statically allocate the hash table to avoid using pointers:
struct entry table[NBUCKET][NENTRY];

// An array of keys that we insert and lookup
int keys[NKEYS];

int nthread = 1;
volatile int done;

// The lock that serializes get()'s.
pthread_mutex_t lock;
pthread_mutex_t lock2;

double
now()
{
 struct timeval tv;
 gettimeofday(&tv, 0);
 return tv.tv_sec + tv.tv_usec / 1000000.0;
}

// Print content of entries in hash table that are in use.
static void
print(void)
{
  int b, i;
  for (b = 0; b < NBUCKET; b++) {
    printf("%d: ", b);
    for (i = 0; i < NBUCKET; i++) {
      if (table[b][i].inuse)
	printf("(%d, %d)", table[b][i].key, table[b][i].value);
    }
    printf("\n");
  }
}

// Insert (key, value) pair into hash table.  
static 
void put(int key, int value)
{
  int b = key % NBUCKET;
  int i;
  // Loop up through the entries in the bucket to find an unused one:
  for (i = 0; i < NENTRY; i++) {
    if (!table[b][i].inuse) {
      assert(pthread_mutex_lock(&lock2) == 0);
      if (!table[b][i].inuse) {
        table[b][i].key = key;
        table[b][i].value = value;
        table[b][i].inuse = 1;
        assert(pthread_mutex_unlock(&lock2) == 0);
        return;
      }
      assert(pthread_mutex_unlock(&lock2) == 0);
    }
  }
  assert(0);
}

// Lookup key in hash table.  The lock serializes the lookups.
static int
get(int key)
{
  int b = key % NBUCKET;
  int i;
  int v = -1;
  for (i = 0; i < NENTRY; i++) {
    if (table[b][i].key == key && table[b][i].inuse)  {
      v = table[b][i].value;
      break;
    }
  }

  return v;
}

static void *
put_thread(void *xa)
{
  long n = (long) xa;
  int i;
  int b = NKEYS/nthread;

  for (i = 0; i < b; i++) {
    put(keys[b*n + i], n);
  }
}

static void *
get_thread(void *xa)
{
  long n = (long) xa;
  int i;
  int k = 0;
  int b = NKEYS/nthread;

  for (i = 0; i < b; i++) {
    int v = get(keys[b*n + i]);
    if (v == -1) k++;
  }
  printf("%ld: %d keys missing\n", n, k);
}

int
main(int argc, char *argv[])
{
  pthread_t *tha;
  void *value;
  long i;
  double t1, t0;

  if (argc < 2) {
    fprintf(stderr, "%s: %s nthread\n", argv[0], argv[0]);
    exit(-1);
  }
  nthread = atoi(argv[1]);

  // Initialize lock
  assert(pthread_mutex_init(&lock, NULL) == 0);
  assert(pthread_mutex_init(&lock2, NULL) == 0);

  // Allocate nthread handles for pthread_join() below.
  tha = malloc(sizeof(pthread_t) * nthread);

  // Generate some keys to insert and then lookup again
  srandom(0);
  assert(NKEYS % nthread == 0);
  for (i = 0; i < NKEYS; i++) {
    keys[i] = random();
    assert(keys[i] > 0);
  }

  t0 = now();
  // Create nthread put threads
  for(i = 0; i < nthread; i++) {
    assert(pthread_create(&tha[i], NULL, put_thread, (void *) i) == 0);
  }
  // Wait until they are all done.
  for(i = 0; i < nthread; i++) {
    assert(pthread_join(tha[i], &value) == 0);
  }
  t1 = now();

  printf("completion time for put phase = %f\n", t1-t0);

  t0 = now();

  // Create nthread get threads
  for(i = 0; i < nthread; i++) {
    assert(pthread_create(&tha[i], NULL, get_thread, (void *) i) == 0);
  }
  // Wait until they are all done.
  for(i = 0; i < nthread; i++) {
    assert(pthread_join(tha[i], &value) == 0);
  }
  t1 = now();

  printf("completion time for get phase = %f\n", t1-t0);
}
