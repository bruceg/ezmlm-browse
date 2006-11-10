#include <unistd.h>
#include "auto_pwd.c"
#include "auto_python.c"

int main(void)
{
  const char* args[] = { auto_python, "-c",
			 "import sys; "
			 "sys.path[0]=sys.argv[1]; "
			 "import main; "
			 "main.main()", auto_pwd, 0 };
  if (chdir(auto_pwd) == 0)
    execv(auto_python, (char**)args);
  return 111;
}
