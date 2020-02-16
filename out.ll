; ModuleID = 'out.ll'

define i8 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i8 
	%out_0x3 = alloca i8, align 1
	store i8 97, i8* %out_0x3, align 1
	%out_0x4 = load i8, i8* %out_0x3, align 1
	store i8 %out_0x4, i8* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0x5 = load i8, i8* %out_0x1_return, align 1
	ret i8 %out_0x5
}

