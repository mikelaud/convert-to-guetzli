#!/usr/bin/python
'''
================================================================================
/*
 * BSD 3-Clause License
 * "convert-to-guetzli" software
 *
 * Copyright (c) June 2017, Mike Oksenenko, mmx.mmx_gmail.com
 * All rights reserved. http://mikelaud.blogspot.com/
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holders nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.
 */
================================================================================
'''
import glob, os, subprocess, sys, time

class Image:
    def __splitFilename(self, filename):
        parts = filename.split('.')
        name = filename if len(parts) <= 1 else filename[:-len(parts[-1])-1]
        extention = '' if len(parts) <= 1 else parts[-1]
        return name, extention
    def __initDimensions(self):
        def __getByIndex(dimensions, index):
            return int(0 if index >= len(dimensions) else dimensions[index])
        if not self.__width or not self.__height:
            dimensions = subprocess.check_output(['gm', 'identify', '-format', '%wx%h', self.getPath()]).rstrip().split('x')
            self.__width = __getByIndex(dimensions, 0)
            self.__height = __getByIndex(dimensions, 1)
    def __init__(self, path):
        self.__path = path
        self.__filename = os.path.basename(path)
        self.__name, self.__extention = self.__splitFilename(self.__filename)
        self.__width = None
        self.__height = None
    def getPath(self):
        return self.__path
    def getFilename(self):
        return self.__filename
    def getName(self):
        return self.__name
    def getExtention(self):
        return self.__extention
    def getWidth(self):
        self.__initDimensions()
        return self.__width
    def getHeigth(self):
        self.__initDimensions()
        return self.__height
    def resizeTo(self, outputDir, downscaleFactor):
        outputName = self.getName() + '.png'
        outputPath = os.path.join(outputDir, outputName)
        inputPath = self.getPath()
        w = self.getWidth() / downscaleFactor
        h = self.getHeigth() / downscaleFactor
        subprocess.check_call(['gm', 'convert', inputPath, '-resize', '%sx%s' % (w,h), '+profile', '*', outputPath])
        return outputPath
    def convertToGuetzli(self, outputDir):
        outputName = self.getName() + '.jpg'
        outputPath = os.path.join(outputDir, outputName)
        inputPath = self.getPath()
        subprocess.check_call(['guetzli', '--quality', '84', inputPath, outputPath])
    def __str__(self):
        w = self.getWidth()
        h = self.getHeigth()
        return '{} => 1) {} {} => 2) {} {} => 4) {} {} => 8) {} {}'.format(self.getFilename(), w, h, w/2, h/2, w/4, h/4, w/8, h/8)

class Arguments:
    def __init__(self, argv):
        def __getByIndex(argv, index):
            return '' if index >= len(argv) else argv[index]
        self.__argv = argv
        self.__count = len(argv)
        self.__scriptName = __getByIndex(argv, 0)
        self.__imagesDirectory = __getByIndex(argv, 1)
    def getCount(self):
        return self.__count
    def isAll(self):
        return 2 == self.getCount() 
    def getScriptName(self):
        return self.__scriptName
    def getImagesDirectory(self):
        return self.__imagesDirectory
    def getHelp(self):
        return 'Usage: {} <directory_with_images>'.format(self.getScriptName())

class Convertor:
    def __findImagesFiles(self, imagesDir):
        def __filterImagesFiles(imagesDir, imagesExt):
            imagesMask = '*.%s' % imagesExt
            imagesPath = os.path.join(imagesDir, imagesMask)
            imagesFiles = glob.glob(imagesPath)
            print 'Found {} files: {}'.format(imagesExt.upper(), len(imagesFiles))
            return imagesFiles
        def __extendImagesFiles(imagesFiles, imagesDir, extention):
                return imagesFiles.extend(__filterImagesFiles(imagesDir, extention))
        imagesFiles = []
        __extendImagesFiles(imagesFiles, imagesDir, 'png')
        __extendImagesFiles(imagesFiles, imagesDir, 'jpg')
        print 'Found TOTAL files: {}'.format(len(imagesFiles))
        return imagesFiles
    def __printImagesDimentions(self, imagesFiles):
        n = 0
        for imageFile in imagesFiles:
            image = Image(imageFile) 
            n = n + 1
            print '{}) {}'.format(n, image)
    def __resizeImages(self, imagesFiles, outputDir, downscaleFactor):
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        resizedImages = []
        count = len(imagesFiles)
        n = 0
        timeN = 0
        timeBegin = time.time()
        for imageFile in imagesFiles:
            image = Image(imageFile) 
            n = n + 1
            m = count - n
            timePerOne = timeN / n
            timeEta = timePerOne * m
            print '{}) {} => {} (resize) ETA: {:.0f} sec'.format(n, image.getFilename(), outputDir, timeEta)
            pngPath = image.resizeTo(outputDir, downscaleFactor)
            resizedImages.append(pngPath)
            timeN = time.time() - timeBegin
        return resizedImages
    def __convertImages(self, imagesFiles, outputDir):
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        count = len(imagesFiles)
        n = 0
        timeN = 0
        timeBegin = time.time()
        for imageFile in imagesFiles:
            image = Image(imageFile) 
            n = n + 1
            m = count - n
            timePerOne = timeN / n
            timeEta = timePerOne * m / 60
            print '{}) {} => {} (convert) ETA: {:.0f} min'.format(n, image.getFilename(), outputDir, timeEta)
            image.convertToGuetzli(outputDir)
            timeN = time.time() - timeBegin
    def __init__(self, arguments):
        self.__arguments = arguments
    def execute(self):
        imagesFiles = self.__findImagesFiles(self.__arguments.getImagesDirectory())
        self.__printImagesDimentions(imagesFiles)
        downscaleFactor = input("Enter a downscale factor (1,2,4,8): ")
        resizedImages = self.__resizeImages(imagesFiles, 'PNG', downscaleFactor)
        self.__convertImages(resizedImages, 'JPEG')

class Application:
    def __checkDirectory(self, directory):
        if not os.path.exists(directory):
            print 'Directory is not found: {}'.format(directory)
            return False
        if not os.path.isdir(directory):
            print 'Path is not directory: {}'.format(directory)
            return False
        print 'Found directory: {}'.format(directory)
        return True
    def __init__(self, argv):
        self.__arguments = Arguments(argv)
        self.__convertor = Convertor(self.__arguments)
    def execute(self):
        if not self.__arguments.isAll():
            print self.__arguments.getHelp()
            exit(10)
        if not self.__checkDirectory(self.__arguments.getImagesDirectory()):
            exit(20)
        self.__convertor.execute()

def main(argv):
    application = Application(argv)
    application.execute()

if __name__ == "__main__":
    main(sys.argv)
