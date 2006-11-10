#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char* argv[])
{
  int pathlen;
  const char* path;
  char buf[1024];
  unsigned long len;
  
  if ((path = getenv("PATH")) == 0)
    return 1;
  if (argc < 2)
    return 1;
  len = strlen(argv[1]);
  do {
    while (*path == ':')
      ++path;
    for (pathlen = 0;
	 path[pathlen] != 0 && path[pathlen] != ':';
	 ++pathlen)
      ;
    if (pathlen > 0 && *path != '.') {
      if (pathlen + 1 + len + 1 > sizeof buf)
	return 1;
      memcpy(buf, path, pathlen);
      buf[pathlen++] = '/';
      memcpy(buf + pathlen, argv[1], len);
      buf[pathlen + len] = 0;
      if (access(buf, X_OK) == 0) {
	buf[pathlen + len] = '\n';
	write(1, buf, pathlen + len + 1);
	return 0;
      }
    }
    path += pathlen;
  } while (*path != 0);
  return 1;
}
