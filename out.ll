; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = icmp eq i32 1, 2
	%out_0x4 = icmp eq i1 0, %out_0x3
	%out_0x5 = icmp ne i1 %out_0x4, 0
	br i1 %out_0x5, label %out_0x6_then, label %out_0x7_iffail
out_0x6_then:
	store i32 1, i32* %out_0x1_return
	br label %out_0x2_returnLabel
out_0x7_iffail:
	store i32 2, i32* %out_0x1_return
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0xa = load i32, i32* %out_0x1_return
	ret i32 %out_0xa
}

