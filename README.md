# NEATPlatformer

This application is a platformer based on Kenneth O' Stanley's paper, found [here](http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf), and is based off Seth Bling's implementation with changes as necessary found [here](https://www.youtube.com/watch?v=qv6UVOQ0F44). This is written in Python 3 with pygame.

### Installation:
Make sure you have python3 and pip installed.
Clone the repo in the directory of your choice, and enter the folder.
Use command line and type `pip install -r requirements.txt` to download pygame.

#### To play the game:
`python3 game.py (filename)` 
The only applicable option for game.py is the level filename. You can use `python3 game.py filename`, or else it will load `level.txt`.

#### To start learning:
`python3 neat.py OPTIONS`

##### OPTIONS-
1. `-l filename`: Choose which level to train or play on. Default level.txt
2. `-i filename`: Which folder to read from and which generation to start from. Should be a folder and a filename, ie. `-i output/gen10.txt` 
4. `-o folder`: Choose which folder to reference for saving newly trained networks. Default is 'output/'
5. `-n x`: Trains with x number of networks at once. Default 1

#### How to create a level to learn or play on:
1. Open a new text file. Name it whatever you want.
2. Make sure you have the number of lines be 12. You can try other amounts, but I think I need to fix it.
3. Put down a W whereever you want a walkable platform or wall. 
4. Put down a T where you want your start player(s) to be.
5. Put down an H where you want your enemies to be.
6. Put down a P where you want your finish platform to be.
7. Make sure that every line has the same number of columns- I like to use an arbitrary character not used, like "e" or a period. 

#### Future additions:
1. Display network of best player
2. Add top genome playback option
