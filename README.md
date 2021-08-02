# Asciir Texture Converter
provides two seperate scripts [ArtToCart](./ArtToCart.py) and [CartToArt](./CartToArt.py) that converts between .art and .cart files.

### Usage
Drag and drop the files that should be converted to the other format.

The files can also be specified as command line arguemnts if the script is called from a terminal.
> \> python ArtToCart.py file1.art file2.art  
> \> python CartToArt.py file1.cart file2.cart

the converted files filename will be the same as the passed files original filename.
> [ArtToCart] file_name.art -> file_name.cart  
> [CartToArt] file_name.cart -> file_name.art 
 
<br><br/>
### Limitations
- a conversion from .art to .cart removes all comments and will therefore not be restored when converting from a .cart file to a .art file. 
Instead there will appear a comment over each section containing the section type.
