@__const.main.out_0x5 = private unnamed_addr constant [19 x i8] c"Wow, Example text!\00", align 1 
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)
; ModuleID = 'out.ll'

define i8 @main() {
out_0x0_entry:
	%out_0x1_return = alloca i8 
	%out_0x3 = alloca i8, align 1
	store i8 101, i8* %out_0x3, align 1
	%out_0x4 = alloca [19 x i8], align 1
	%out_0x5 = bitcast [19 x i8]* %out_0x4 to i8*
	call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 %out_0x5, i8* align 1 getelementptr inbounds ([19 x i8], [19 x i8]* @__const.main.out_0x5, i32 0, i32 0), i64 19, i1 false)
	%out_0x6 = alloca [19 x i8]*, align 1
	store [19 x i8]* %out_0x4, [19 x i8]** %out_0x6, align 1
	%out_0x7 = load [19 x i8]*, [19 x i8]** %out_0x6, align 1
	%out_0x8 = getelementptr [19 x i8], [19 x i8]* %out_0x7, i64 0, i64 0
	%out_0x9 = load i8, i8* %out_0x8, align 1
	store i8 %out_0x9, i8* %out_0x1_return, align 1
	br label %out_0x2_returnLabel
out_0x2_returnLabel:
	%out_0xa = load i8, i8* %out_0x1_return, align 1
	ret i8 %out_0xa
}

