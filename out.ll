; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = icmp eq i32 1, 2
	%out_0x4 = icmp ne i1 %out_0x3, 0
	br i1 %out_0x4, label %out_0x5_then, label %out_0x6_iffail
out_0x5_then:
	store i32 1, i32* %out_0x1_return
	br label %out_0x2_returnLabel
out_0x6_iffail:
	store i32 2, i32* %out_0x1_return
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0x9 = load i32, i32* %out_0x1_return
	ret i32 %out_0x9
}

