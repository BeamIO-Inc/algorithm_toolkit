About the Algorithm Toolkit
===========================

Why does this exist?
--------------------
Algorithms on this site can benefit people and industries. From helping investors predict markets more accurately to making farmers more productive, image processing algorithms are revolutionizing the way we live and work. For too long these have been locked away in academia or in private companies. We thought it was time to bring them to the world.

What are algorithms?
--------------------
Images are data. For each pixel in an image you may have hundreds or even thousands of data values captured by sophisticated sensor equipment, or attached by software during image processing. Algorithms are basically mathematical equations applied to the data contained in images in order to reveal aspects of the image that may not normally be visible.

What is the ATK?
----------------
Researchers all over the world have written software programs that apply algorithms to images. Up to now, those programs have been written in lots of different ways using lots of different software tools, and haven’t been able to talk to other programs written by other researchers. Our ATK creates a way for anyone who develops one of these software programs to make it available in a standard way.

Doesn't sound like such a big deal.
-----------------------------------
Typically, many algorithms are used in sequence to process an image. For example, if you want to show vegetation health from pictures taken from a satellite, you might:

* Download the pictures from the satellite’s feed
* Stitch together the pictures into a single orthomosaic image
* Perform a calculation called NDVI to show amounts of chlorophyll in each pixel of that image
* Apply a color scale to the resulting pixels (which otherwise would be grayscale); maybe green to red
* Export the image to the web

Each of these steps might be done by a single algorithm, but how does each step know what to do with the stuff that came before it? And how does it know what to provide the next step?

The ATK creates a way to define an algorithm “chain” with standard inputs and outputs. That way, when you create an algorithm you know what you’ll be getting in and can tell other developers what you’re providing out.
