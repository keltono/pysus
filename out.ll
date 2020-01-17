; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca i32
	store i32 0, i32* %out_0x3
	%out_0x4 = icmp slt i32 %out_0x3, 10
	%out_0x5 = icmp ne i1 %out_0x4, 0
	br i1 %out_0x5, label %out_0x6_whileBody, label %out_0x7_whileFail
out_0x6_whileBody:
	%out_0x9 = add i32 %out_0x3, 1
	store i32 %out_0x9, i32* %out_0x3
	%out_0xa = icmp slt i32 %out_0x3, 10
	%out_0x5_inside = icmp ne i1 %out_0xa, 0
	br i1 %out_0x5_inside, label %out_0x6_whileBody, label %out_0x7_whileFail
out_0x7_whileFail:
	store i32 %out_0x3, i32* %out_0x1_return
out_0x2_returnLabel:
	%out_0xb = load i32, i32* %out_0x1_return
	ret i32 %out_0xb
}

