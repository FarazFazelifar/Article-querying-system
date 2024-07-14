# Article-querying-system
A program to search and retrieve related information to a user query from 3 major health publications.
The articles are from PubMed, Arxiv and Scopus.

## How to use
this repository has 2 Python files which can be used to search for articles.
### Search with API
The search_with_API program allows you to query your desired information 
using APIs. In this method, the abstract and doi of some articles might be missing.
to use this file, you first need to install the libraries using this command:

 ```pip install requests pandas```

 then you can simply run the program and search for the articles you want.

### Search with library
The search_with_library uses the packages provided by these publications instead of using their APIs.
Just like the previous method, some data might be missing. To use this script, you must first set up the 
initialization file. To do this, you must copy the ```config.ini``` file into your home directory. On Windows,
this is typically located at ```C:\Users\YourUsername\.scopus\```. Then you will need to install the required packages with 
this command:

```pip install arxiv biopython pybliometric```

after that, you can run the program and input your query.

**It is recommended to use both methods, since each method can have some missing data that the other method might provide!**
