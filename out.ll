; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca i32, align 1
	store i32 42, i32* %out_0x3, align 1
	%out_0x5 = alloca i32*, align 1
	store i32* %out_0x3, i32** %out_0x5, align 1
	%out_0x6 = load i32*, i32** %out_0x5, align 1
	%out_0x8 = sub i32 0, 1
	%out_0x7 = getelementptr i32, i32* %out_0x6, i32 %out_0x8
	store i32* %out_0x7, i32** %out_0x5, align 1
	%out_0xa = load i32*, i32** %out_0x5, align 1
	%out_0x9 = load i32, i32* %out_0xa, align 1
	store i32 %out_0x9, i32* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0xb = load i32, i32* %out_0x1_return, align 1
	ret i32 %out_0xb
}

