#include "kernel/types.h"
#include "user.h"
#include "pstat.h"

int
main(int argc, char **argv)
{
  struct pstat ps;
  if (getpinfo(&ps) < 0) {
    printf("getpinfo failed\n");
    exit(1);
  }
  printf("PID\tinuse\ttickets\tticks\n");
  for (int i = 0; i < NPROC; i++) {
    if (ps.inuse[i]) {
      printf("%d\t%d\t%d\t%d\n", ps.pid[i], ps.inuse[i], ps.tickets[i], ps.ticks[i]);
    }
  }
  exit(0);
}
