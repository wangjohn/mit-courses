{
    numprimes = 3000;
    checkprimes = primes(numprimes);
    solution_count = 0;
    for(i=1, numprimes,
        cprime = checkprimes[i];
        for (j=1, cprime,
            if (Mod(j^3 - 2, cprime) == Mod(0, cprime), 
                solution_count ++;
                print(cprime);
                break;
            );
        );
    );
    print("Density:", solution_count/numprimes);
}
