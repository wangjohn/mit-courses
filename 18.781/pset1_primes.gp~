{
    for(i=1, 10,
        p = 0;
        p4k3 = 0;
        p4k1 = 0;
        forprime(x=1, i*10000,
            p ++;
            if((x%4) == 3, p4k3 ++, p4k1 ++);
        );
        xlogx = round(i*10000/log(i*10000));
        print("x = ", i*10000);
        print("Primes: ", p);
        print("4k+1 Primes: ", p4k1);
        print("4k+3 Primes: ", p4k3);
        print("x/log(x): ", xlogx);
        print(" ");
    )
}
