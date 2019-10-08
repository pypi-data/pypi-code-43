Ans="""
interface child

{
public void egg();
}
public class create_animal implements child
{
public void reptiles()
{
System.out.println("Reptiles animals have scales,dark skin,cold blooded");
}

public void birds()
{
System.out.println("birds have feathers wings");
}

public void fish()
{
System.out.println("Fish have scales,fins, breathe underwater using gills");
}

public void egg()
{
System.out.println("reptiles,bird and fish lay eggs");
}
 
}

class animalm{

    
    public static void main(String[] args) {
        {

create_animal a1=new create_animal();
a1.reptiles();
a1.birds();
a1.fish();
a1.egg();

}
    }
    
}


"""