; ModuleID = 'out.ll'

define i32 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i32 
	%out_0x3 = alloca [2 x i32], align 4
	%out_0x4_arr_init = getelementptr [2 x i32], [2 x i32]* %out_0x3, i64 0, i64 0 
	store i32 1, i32* %out_0x4_arr_init, align 1
	%out_0x4_arr_0 = getelementptr i32, i32* %out_0x4_arr_init, i64 1
	store i32 2, i32* %out_0x4_arr_0, align 1
	%out_0x5 = alloca [2 x i32], align 4
	%out_0x6_arr_init = getelementptr [2 x i32], [2 x i32]* %out_0x5, i64 0, i64 0 
	store i32 3, i32* %out_0x6_arr_init, align 1
	%out_0x6_arr_0 = getelementptr i32, i32* %out_0x6_arr_init, i64 1
	store i32 4, i32* %out_0x6_arr_0, align 1
	%out_0x7 = alloca [2 x [2 x i32]*], align 4
	%out_0x8_arr_init = getelementptr [2 x [2 x i32]*], [2 x [2 x i32]*]* %out_0x7, i64 0, i64 0 
	store [2 x i32]* %out_0x3, [2 x i32]** %out_0x8_arr_init, align 1
	%out_0x8_arr_0 = getelementptr [2 x i32]*, [2 x i32]** %out_0x8_arr_init, i64 1
	store [2 x i32]* %out_0x5, [2 x i32]** %out_0x8_arr_0, align 1
	%out_0x9 = alloca [2 x [2 x i32]*]*, align 1
	store [2 x [2 x i32]*]* %out_0x7, [2 x [2 x i32]*]** %out_0x9, align 1
	%out_0xa = load [2 x [2 x i32]*]*, [2 x [2 x i32]*]** %out_0x9, align 1
	%out_0xb = getelementptr [2 x [2 x i32]*], [2 x [2 x i32]*]* %out_0xa, i64 0, i64 1
	%out_0xc = load [2 x i32]*, [2 x i32]** %out_0xb, align 1
	%out_0xd = getelementptr [2 x i32], [2 x i32]* %out_0xc, i64 0, i64 1
	%out_0xe = load i32, i32* %out_0xd, align 1
	store i32 %out_0xe, i32* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0xf = load i32, i32* %out_0x1_return, align 1
	ret i32 %out_0xf
}

