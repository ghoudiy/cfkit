for s in[*open(0)][1:]:
 r=i=0
 while i<int(s):r+=1;i+=r%10!=3and r%3>0
 print(r)
