#include "kernel/types.h"
#include "user.h"
#include "pstat.h"

int
do_test(int samples, int interval, int t0, int t1, int t2)
{
  int tickets[3] = {t0, t1, t2};
  int pids[3];

  for (int i = 0; i < 3; i++) {
    int pid = fork();
    if (pid < 0) {
      printf("fork failed\n");
      return -1;
    }
    if (pid == 0) {
      settickets(tickets[i]);
      for (;;)
        ;
    }
    pids[i] = pid;
  }

  // imprime cabeçalho 
  printf("=== TEST tickets %d:%d:%d samples=%d interval=%d ===\n", t0, t1, t2, samples, interval);
  printf("time,ticksA,ticksB,ticksC\n");

  for (int s = 0; s < samples; s++) {
    pause(interval);
    struct pstat ps;
    if (getpinfo(&ps) < 0) {
      printf("getpinfo failed\n");
      break;
    }
    int t[3] = {0,0,0};
    for (int i = 0; i < NPROC; i++) {
      for (int j = 0; j < 3; j++) {
        if (ps.pid[i] == pids[j])
          t[j] = ps.ticks[i];
      }
    }
    printf("%d,%d,%d,%d\n", s, t[0], t[1], t[2]);
  }

  for (int i = 0; i < 3; i++)
    kill(pids[i]);
  for (int i = 0; i < 3; i++)
    wait(0);

  return 0;
}

int
main(int argc, char **argv)
{
  int samples = 60;
  int interval = 100;

  if (argc >= 3) {
    samples = atoi(argv[1]);
    interval = atoi(argv[2]);
  }

  do_test(samples, interval, 30, 20, 10);
  do_test(samples, interval, 60, 40, 20);
  do_test(samples, interval, 60, 30, 10);
  do_test(samples, interval, 20, 20, 20);
  do_test(samples, interval, 90, 5, 5);
  do_test(samples, interval, 45, 30, 15);

  exit(0);
}
