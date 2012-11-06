public void main(String[] args) {

	public int[] numberBases(String equation){
		equation = equation.replaceAll("\\s", "") // remove whitespace
		Pattern regexPattern = Pattern.compile("([0-9]+)\\+([0-9]+)=([0-9]+)");
		Matcher regexMatcher = regexPattern.matcher(equation);
		int a = Integer.parseInt(regexMatcher.find());
		int b = Integer.parseInt(regexMatcher.find());
		int c = Integer.parseInt(regexMatcher.find());
		
		int [] validList = int [9];
		counter = 0;
		for (int i=2; i<=10; i++){
			if (i > c && ((a + b) % i) == c){
				validList[counter] = i;
				counter += 1;	
			}
		}
		
		int [] output = int [counter];
		for (int i=0; i<counter; i++){
			output[i] = validList[i];
		}
		return output;

	} 
}
