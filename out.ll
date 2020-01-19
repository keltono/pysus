; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca i32
	store i32 42, i32* %out_0x3
	%out_0x5 = alloca i32*
	store i32* %out_0x3, i32** %out_0x5
	%out_0x7 = load i32*, i32** %out_0x5
	%out_0x6 = load i32, i32* %out_0x7
	store i32 %out_0x6, i32* %out_0x1_return
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0x8 = load i32, i32* %out_0x1_return
	ret i32 %out_0x8
}

