# mini_pics
I've always wanted a tiny picture frame that could showcase interesting prints collected from around the web.

This project uses an [Adafruit PyPortal](https://www.adafruit.com/product/4116) to display some low resolution images that are stored on an SD card.

*Update* 10/24 - added version ```codev2.py``` that calls a server to refresh images.

There's also a case you 3D print to enclose the device. Mine sits next to my screen, propped up by the USB cable powering the PyPortal.

The screen is best at displaying high contrast images. Here are sources for good images:

* Woodblock prints from the [Plantin-Moretus Museum](https://collectie.antwerpen.be/impressedbyplantin/all-woodcuts)
* [Japanese Woodblock prints](https://ukiyo-e.org)
* Gustave Dore's London series at the [British Library](https://www.bl.uk/collection-items/london-illustrations-by-gustave-dor#)
* The [Tate](https://www.tate.org.uk/art/artworks/hogarth-gin-lane-t01799)
* [Albrecht Durer](https://www.albrecht-durer.org)
* The Rijks Museum's [RijksStudio](https://www.rijksmuseum.nl/en/rijksstudio)
* [Public Domain Review](https://publicdomainreview.org/explore/)

Note that each images needs to be cropped to 240 x 320 px and saved as a Windows Bitmap [howto](https://learn.adafruit.com/creating-your-first-tilemap-game-with-circuitpython/indexed-bmp-graphics). If you don't save them as exactly this they'll fail to load and you may overflow the PyPortal's fragile memory.

This is by far the most frustrating part of using this. In addition to the tutorial above, a few notes:

* I use a Mac; if I don't see a preview of a .bmp file on my machine I know it will not load on the PyPortal and cause it to crash
* When exporting a .bmp in Gimp, I have to set the "Run-Length Encoded" option to true in order to create a working file

Some sample images to get you started are included in a folder called *topics*.
