; ModuleID = 'out.ll'

define i32 @add1(i32 %out_0x0) {
out_0x1_entry:
	%out_0x2 = add i32 %out_0x0, 1
	ret i32 %out_0x2
}

define i32 @main() {
out_0x3_entry:
	%out_0x4 = call i32 @add1(i32 3)
	ret i32 %out_0x4
}

