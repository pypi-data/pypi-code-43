Ans="""
    #include<stdio.h>
    int main(){
        //1
        int total;
        int i;
        
        //2
        int positiveSum = 0;
        int negativeSum = 0;
        
        //3
        printf("How many numbers you want to add : ");
        scanf("%d",&total);
        
        //4
        int numbers[total];
        
        //5
        for(i=0; i<total; i++){
            printf("Enter number %d : ",(i+1));
            scanf("%d",&numbers[i]);
        }
        
        //6
        for(i=0 ; i<total ; i++){
           if(numbers[i] < 0){
             negativeSum += numbers[i];
           }else{
             positiveSum += numbers[i];
           }
        }
     
        //7
        printf("You have entered : \n");
        for(i=0 ; i<total; i++){
         printf("%d ",numbers[i]);
        }
     
        //8
        printf("\nPositive numbers sum : %d",positiveSum);
        printf("\nNegative numbers sum : %d\n",negativeSum);
     
    }

"""