{
    modulus = 23^2;
    modulusphi = eulerphi(modulus);
    for(i=2, modulus - 1,
        if(modulusphi == znorder(Mod(i, modulus)), print(i));
    );
}
