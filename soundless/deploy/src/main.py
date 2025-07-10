import re
import subprocess

if __name__ == "__main__":

	struct_ty = "S[0-9]+"
	ptr_ty = "(%s|void)\\*+" % struct_ty
	field_name = "f[0-9]+"
	obj_name = "o[0-9]+"
	ptr_name = "p[0-9]+"

	struct_def = "typedef struct \\{ (%s %s; )+\\} %s;" % (ptr_ty, field_name, struct_ty)
	obj_def = "%s %s = \\{0\\};" % (struct_ty, obj_name)
	ref = "%s %s = &((%s(\\.%s)?)|(%s->%s));" % \
		(ptr_ty, ptr_name, obj_name, field_name, ptr_name, field_name)
	move = "(\\*|(%s ))%s = \\*?%s;" % (ptr_ty, ptr_name, ptr_name)

	stmt = "(%s)|(%s)|(%s)|(%s)" % (struct_def, obj_def, ref, move)

	print("You can write C statements satisfying the following constraint:")
	print(stmt)
	stmt = re.compile(stmt)

	with open("/home/ctf/flag", 'r') as fd:
		flag = fd.read().strip()

	src = """
#include <stdio.h>
char flag[] = "%s";
char hello[] = "world";
char me[] = "2019";
char andy[] = "Andy";
char universe[] = "42";

void say_hello(void* s)
{
	printf("Hello %%s!", (const char*)s);
}

int main()
{
	void* p0 = flag;
	void* p1 = hello;
	void* p2 = me;
	void* p3 = andy;
	void* p4 = universe;
""" % flag

	while True:
		line = input()
		if line == "EOF":
			break
		if not re.fullmatch(stmt, line):
			print("Invalid statement!")
			continue
		src += '\t'
		src += line
		src += '\n'

	src += """
	say_hello(p42);
	return 0;
}"""

	with open("/tmp/program.c", "w") as fd:
		fd.write(src)

	subprocess.run(["clang", "-Wall", "-Wno-unused-variable", "-Werror", "-flto", "-g", "-O0",
		"-c", "/tmp/program.c", "-o", "/tmp/program.o"],
		check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.run(["/home/ctf/SVFChecker/build/checker", "/tmp/program.o"], check=True,
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.run(["clang", "-Wall", "-Wno-unused-variable", "-Werror", "-g", "-O0",
		"/tmp/program.c", "-o", "/tmp/program"],
		check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.run(["/tmp/program"], stderr=subprocess.DEVNULL)