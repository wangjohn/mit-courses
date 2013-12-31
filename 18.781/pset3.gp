{
    count = 0;
    m = 1;
    while(count<10,
        p = 6*m+1;
        q = 12*m+1;
        r = 18*m+1;
        if (isprime(p) && isprime(q) && isprime(r), 
            print(p*q*r);
            count ++;
            );
        m ++;
    )
}
