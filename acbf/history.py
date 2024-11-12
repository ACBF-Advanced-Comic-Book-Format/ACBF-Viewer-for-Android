"""history.py - tracks history of open files (CONFIG_DIR/history.xml).

Copyright (C) 2011-2024 Robert Kubik
https://github.com/GeoRW/ACBF
"""

# -------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# -------------------------------------------------------------------------


import os.path
import lxml.etree as xml
from kivy.utils import platform

if platform == 'android':
  from jnius import autoclass
  from jnius import cast
    
  PythonActivity = autoclass('org.kivy.android.PythonActivity')
  Uri = autoclass('android.net.Uri')
  DocumentFile = autoclass('androidx.documentfile.provider.DocumentFile')
else:
  print("Not running on Android ...")

try:
  from . import constants
except Exception:
  import constants

class History():

  def __init__(self, config_dir):
      self.config_dir = config_dir
      self.hist_file_path = os.path.join(self.config_dir, 'history.xml');
      self.load_history()
      self.cleanup_history()

  def create_new_tree(self):
      self.tree = xml.Element("history")

      version = xml.SubElement(self.tree, "version")
      version.text = constants.VERSION

      self.save_history()
      self.load_history()

      #print(self.tree.find("bg_color_override").text)
      #print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))

  def load_history(self):
      print('load_history')
      try:
        self.tree = xml.parse(source = self.hist_file_path)
        #print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
      except:
        self.create_new_tree()
        f = open(self.hist_file_path, 'w')
        f.write(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
        f.close()

  def save_history(self):
      print('save_history')
      f = open(self.hist_file_path, 'w')
      #print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
      f.write(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
      f.close()

  def get_book_details(self, book_path):
      for book in self.tree.findall("file"):
        if book.get("path") == str(book_path):
          return (int(book.find("current_page").text), int(book.find("current_frame").text), int(book.find("current_zoom").text), int(book.find("current_language").text))
      return (1, 1, 0, 0)

  def set_book_details(self, book_path, current_page, current_frame, current_zoom, current_language):
      for book in self.tree.findall("file"):
        if book.get("path") == str(book_path):
          book.find("current_page").text = str(current_page)
          book.find("current_frame").text = str(current_frame)
          book.find("current_zoom").text = str(current_zoom)
          book.find("current_language").text = str(current_language) 
          return

      tree = xml.Element("history")
      version = xml.SubElement(tree, "version")
      version.text = constants.VERSION
      
      # copy old ones
      for book in self.tree.findall("file"):
        new_book = xml.SubElement(tree, "file", path=book.get("path"))
        new_page = xml.SubElement(new_book, "current_page")
        new_page.text = book.find("current_page").text
        new_page = xml.SubElement(new_book, "current_frame")
        new_page.text = book.find("current_frame").text
        new_page = xml.SubElement(new_book, "current_zoom")
        new_page.text = book.find("current_zoom").text
        new_page = xml.SubElement(new_book, "current_language")
        new_page.text = book.find("current_language").text
      

      # add new book
      new_book = xml.SubElement(tree, "file", path=str(book_path))
      new_page = xml.SubElement(new_book, "current_page")
      new_page.text = str(current_page)
      new_page = xml.SubElement(new_book, "current_frame")
      new_page.text = str(current_frame)
      new_page = xml.SubElement(new_book, "current_zoom")
      new_page.text = str(current_zoom)
      new_page = xml.SubElement(new_book, "current_language")
      new_page.text = str(current_language)

      self.tree = tree

      #print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))

  def delete_book(self, path):
      print('Delete book:', path)
      for book in self.tree.findall("file"):
        #print(book.get("path"), path)
        if book.get("path") == str(path):
          book.getparent().remove(book)
      return

  def cleanup_history(self):
    print('cleanup_history')
    deleted = False
    #print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
    for book in self.tree.findall("file"):
      if platform == 'android':
        uri = Uri.parse(book.get("path"))
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        documentfile = DocumentFile.fromSingleUri(currentActivity, uri)
        if not documentfile.exists():
          #print('Not exists:', book.get("path"))
          self.delete_book(str(book.get("path")))
          deleted = True
      elif not os.path.exists(book.get("path")):
        self.delete_book(str(book.get("path")))
        deleted = True

    print(xml.tostring(self.tree, encoding='unicode', pretty_print=True))
    if deleted:
      self.save_history()

