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
import unittest, os, subprocess
import convert_to_guetzli as ctg
from mock import patch

class Test(unittest.TestCase):

    @staticmethod
    def getFilePath(fileName):
        pwd = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pwd, fileName)

    def testGraphicsMagick_getDimensions(self):
        imagePath = Test.getFilePath('convert-to-guetzli.png') 
        width, height = ctg.GraphicsMagick.getDimensions(imagePath)
        self.assertEqual(477, width)
        self.assertEqual(366, height)

    def testGraphicsMagick_resize(self):
        imagePath = Test.getFilePath('convert-to-guetzli.png')
        outputPath = Test.getFilePath('testGraphicsMagick_resize.png')
        newSize = 100
        ctg.GraphicsMagick.resize(imagePath, outputPath, newSize, newSize)
        outputImage = ctg.Image(outputPath)
        self.assertEqual(newSize, outputImage.getWidth())
        self.assertEqual(77, outputImage.getHeight())

    def testGuetzli(self):
        imagePath = Test.getFilePath('convert-to-guetzli.png')
        outputPath = Test.getFilePath('testGuetzli.png')
        with patch.object(subprocess, 'check_call', return_value=0) as mock_method:
            ctg.Guetzli.convert(imagePath, outputPath)
        args = ['guetzli', '--quality', '84', imagePath, outputPath]
        mock_method.assert_called_once_with(args)

    def testArguments(self):
        scriptName = 'convert_to_guetzli.py'
        imagesDir = 'images_dir'
        argv = [scriptName, imagesDir]
        arguments = ctg.Arguments(argv)
        self.assertEqual(len(argv), arguments.getCount())
        self.assertTrue(arguments.isAll())
        self.assertEqual(scriptName, arguments.getScriptName())
        self.assertEqual(imagesDir, arguments.getImagesDirectory())
        self.assertIn(scriptName, arguments.getHelp())

    def testImage(self):
        imageExtention = 'png'
        imageName = 'convert-to-guetzli'
        imageFilename = '{}.{}'.format(imageName, imageExtention)
        imagePath = Test.getFilePath(imageFilename)
        image = ctg.Image(imagePath)
        self.assertEqual(imagePath, image.getPath())
        self.assertEqual(imageFilename, image.getFilename())
        self.assertEqual(imageName, image.getName())
        self.assertEqual(imageExtention, image.getExtention())

    def testImage_resizeTo(self):
        imageName = 'convert-to-guetzli'
        imagePath = Test.getFilePath('{}.png'.format(imageName))
        outputPath = Test.getFilePath('{}.png'.format(imageName))
        outputDir = os.path.dirname(outputPath)
        with patch.object(ctg.GraphicsMagick, 'resize', return_value=None) as mock_method:
            image = ctg.Image(imagePath)
            image.resizeTo(outputDir, 2)
        mock_method.assert_called_once_with(imagePath, outputPath, 238, 183)
    
    def testImage_convertToGuetzli(self):
        imageName = 'convert-to-guetzli'
        imagePath = Test.getFilePath('{}.png'.format(imageName))
        outputPath = Test.getFilePath('{}.jpg'.format(imageName))
        outputDir = os.path.dirname(outputPath)
        with patch.object(ctg.Guetzli, 'convert', return_value=None) as mock_method:
            image = ctg.Image(imagePath)
            image.convertToGuetzli(outputDir)
        mock_method.assert_called_once_with(imagePath, outputPath)

    def testApplication(self):
        scriptName = 'convert_to_guetzli.py'
        argv = [scriptName]
        application = ctg.Application(argv)
        with self.assertRaises(SystemExit) as systemExit:
            application.execute()
        self.assertEqual(10, systemExit.exception.code)

if __name__ == '__main__':
    unittest.main()
