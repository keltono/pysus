; ModuleID = 'out.ll'

define i32 @cool(i32 %out_0x0) {
out_0x1_entry:
	%out_0x2_return = alloca i32 
	%out_0x4 = alloca i1, align 1
	store i1 0, i1* %out_0x4, align 1
	%out_0x5 = alloca i32, align 1
	store i32 2, i32* %out_0x5, align 1
	%out_0x6 = icmp eq i32 1, 1
	%out_0x7 = icmp ne i1 %out_0x6, 0
	br i1 %out_0x7, label %out_0x8_then, label %out_0x9_iffail
out_0x8_then:
	%out_0xb = load i1, i1* %out_0x4, align 1
	store i1 1, i1* %out_0x4, align 1
	br label %out_0xc_ifdone
out_0x9_iffail:
	%out_0xd = load i1, i1* %out_0x4, align 1
	store i1 0, i1* %out_0x4, align 1
	br label %out_0xc_ifdone
out_0xc_ifdone:
	br label %out_0x3_returnLabel
out_0x3_returnLabel:
	%out_0xe = load i32, i32* %out_0x2_return, align 1
	ret i32 %out_0xe
}

