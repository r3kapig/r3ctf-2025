from PIL import Image
import subprocess

svg_content=input("SVG content: ")
assert len(svg_content)<1024, "too long"
assert "flag" not in svg_content, "......" # This is unrelated to the solution

with open("exp.svg","w") as f:
    f.write(svg_content)

def check(binary, color):
    process=subprocess.run(["./"+binary, "exp.svg", "-o", "exp.png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert process.returncode==0, "runtime error"
    img=Image.open("exp.png")
    assert img.size==(10,10), "incorrect size"
    assert img.tobytes()==100*color, "incorrect color"

checks=[("stretch", b"\x00\x00\x00"), ("buster", b"\xff\x00\x00"), ("bullseye", b"\x00\xff\x00"), ("bookworm", b"\x00\x00\xff")]
for i in checks:
    check(*i)

with open("flag.txt") as f:
    print(f.read())