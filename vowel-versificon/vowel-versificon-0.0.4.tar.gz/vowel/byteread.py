Ans="""

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#define size 1
#define numelem 30	
void main()
{
FILE *fd=NULL;
char buff[100];
memset(buff,0,sizeof(buff));
fd=fopen("test.txt","rw+");
if(NULL==fd)
{
printf("\nfopen() error!!!\n");
return;
}
printf("\nfile opened successfully\n");
if(size*numelem!=fread(buff,size,numelem,fd))
{
printf("\nfread() failed!!!\n");
return;
}

printf("\nSome bytes successfully read through fread()\n");
printf("\nthe bytes read are [%s]\n",buff);
if(0!=fseek(fd,0,SEEK_CUR))
{
printf("\n fseek() failed \n");
return;
}
printf("\n fseek() successful\n");
fclose(fd);
printf("\n filestream closed through fclose() \n");

}

"""