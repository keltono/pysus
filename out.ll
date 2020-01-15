; ModuleID = 'out.ll'

define i32 @main() {
entry:
	%out_0x0 = add i32 2, 2
	%out_0x1 = alloca i32
	store i32 %out_0x0, i32* %out_0x1
	store i32 2, i32* %out_0x1
	%out_0x2 = load i32, i32* %out_0x1
	ret i32 %out_0x2
}

