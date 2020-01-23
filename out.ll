; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca i32, align 1
	store i32 42, i32* %out_0x3, align 1
	%out_0x5 = alloca i32*, align 1
	store i32* %out_0x3, i32** %out_0x5, align 1
	%out_0x6= load i32*, i32** %out_0x5
	store i32 13, i32* %out_0x6, align 1
	%out_0x7 = load i32, i32* %out_0x3, align 1
	store i32 %out_0x7, i32* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0x8 = load i32, i32* %out_0x1_return, align 1
	ret i32 %out_0x8
}

