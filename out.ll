; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca [5 x i32], align 4
	%out_0x4_arr_init = getelementptr [5 x i32], [5 x i32]* %out_0x3, i64 0, i64 0 
	store i32 1, i32* %out_0x4_arr_init, align 1
	%out_0x4_arr_0 = getelementptr i32, i32* %out_0x4_arr_init, i64 1
	store i32 2, i32* %out_0x4_arr_0, align 1
	%out_0x4_arr_1 = getelementptr i32, i32* %out_0x4_arr_init, i64 2
	store i32 3, i32* %out_0x4_arr_1, align 1
	%out_0x4_arr_2 = getelementptr i32, i32* %out_0x4_arr_init, i64 3
	store i32 4, i32* %out_0x4_arr_2, align 1
	%out_0x4_arr_3 = getelementptr i32, i32* %out_0x4_arr_init, i64 4
	store i32 5, i32* %out_0x4_arr_3, align 1
	%out_0x5 = alloca [5 x i32]*, align 1
	store [5 x i32]* %out_0x3, [5 x i32]** %out_0x5, align 1
	store i32 0, i32* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0x6 = load i32, i32* %out_0x1_return, align 1
	ret i32 %out_0x6
}

