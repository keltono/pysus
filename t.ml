let rec x t = 
    match t<4 with
    | true -> 1
    | false -> x (t-1) + x (t-2) + x (t-3)
