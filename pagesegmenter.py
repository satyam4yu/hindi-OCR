import cv2
import numpy as np
from matplotlib import pyplot as plt
import os

class word_finder:
    
	def __init__(self,img):
		self.img = cv2.imread(img,0)
		self.img_color = cv2.imread(img)
		self.img = cv2.resize(self.img,(0,0), fx=0.75, fy=0.75)
		self.img_color = cv2.resize(self.img_color,(0,0), fx=0.75, fy=0.75)
		self.cimg = cv2.Canny(self.img,200,250)
		(t,self.cimg) = cv2.threshold(self.img,160,255,cv2.THRESH_BINARY)
		self.rows = self.img.shape[0]
		self.cols = self.img.shape[1]



	def find_words(self,l_limit,r_limit):
		print('obtaining words....')
		line_count_matrix = []  #identifies number of white pixels in line
		line_matrix = []  #contains co-ordinates to draw boxes around lines
		#print("obtaining line_count")

		for y in range(0,self.rows -1):
			count = 0
			for x in range(l_limit,r_limit):
				if self.cimg[y][x] == 255:
					count += 1
			line_count_matrix.append(count)
		#print(" obtained line_count") 		
		
		#print("obtaining lines")
		y = 0
		while y < len(line_count_matrix) - 1 :
			if line_count_matrix[y] > 30:
				line_matrix.append(y)
				for y2 in range(y + 3, len(line_count_matrix) - 1):
					if line_count_matrix[y2] < 8:
						line_matrix.append(y2)
						y = y2
						break
			y +=1
		#print(len(line_matrix))
		#print("obtained lines")	
		#print("obtaining count for words")
		self.line_matrix = line_matrix
		count = 0
		x_count_matrix = []
		word_matrix = []
		for i in range(0,len(line_matrix)- 1,2):	
			x_count_matrix.append([])
			for x in range(l_limit,r_limit):
				count = 0
				for y in range(line_matrix[i],line_matrix[i+1]):
					if self.cimg[y][x] == 255:
						count += 1			
				x_count_matrix[i//2].append(count)
		#print("count for words has been obtained")		
		self.x_count_matrix = x_count_matrix	
		#print(len(x_count_matrix[0]))
		for y in range(0,len(x_count_matrix)-1):
			word_matrix.append([])
			#word_matrix[y].append(l_limit)
			x = 0
			while x < len(x_count_matrix[y]) - 5:
				if x_count_matrix[y][x] + x_count_matrix[y][x+1] + x_count_matrix[y][x+2] + x_count_matrix[y][x+3] < 5:
					word_matrix[y].append(x + l_limit)
					for x2 in range(x+4,len(x_count_matrix[y])-5):
						if x_count_matrix[y][x2] > 1:
							word_matrix[y].append(x2 + l_limit)
						x = x2
						break
				x += 4
			word_matrix[y].append(r_limit)
		self.word_matrix = word_matrix 	
		word_array = []
		
		for y in range(0,len(self.line_matrix)-2,2):
			for x in range(1,len(self.word_matrix[y//2])-2,2):
				if self.word_matrix[y//2][x+1] - self.word_matrix[y//2][x] > 4: #change 4 to a smaller number to include punctuations.
					word_array.append(self.word_matrix[y//2][x] - 3)
					word_array.append(self.line_matrix[y]-5)
					word_array.append(self.word_matrix[y//2][x+1] + 3)
					word_array.append(self.line_matrix[y+1]+2)
		self.word_array = word_array   #ultimate array to find words, formate (x1,y1,x2,y2) top left and bottom right corner of word
		#print("word array has been created")				
		print("words obtained")
	
	def show_lines(self,l_limit,r_limit):
		for y in range(0,len(self.line_matrix) -2,2):
			cv2.rectangle(self.img,(l_limit,self.line_matrix[y] - 5),(r_limit,self.line_matrix[y+1]),0,1)
		cv2.imshow('Image',self.img)
		cv2.waitKey(0)
	
	def show_words(self):
		print("drawing words")
		for i in range(0,len(self.word_array)-1,4):
			cv2.rectangle(self.img_color,(self.word_array[i],self.word_array[i+1]),(self.word_array[i+2],self.word_array[i+3]),0,1)

	def show_image(self):	
		cv2.imshow('Image',self.img_color)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def store_words(self,no_words):
		print('storing words.....')
		for i in range(0,len(self.word_array),4):
			cropped = self.img_color[self.word_array[i+1]:self.word_array[i+3],self.word_array[i]:self.word_array[i+2]]
			cv2.imwrite('words/'+str(no_words + i/4)+'.png',cropped)
		print('words have been stored ......')

################################ HANDLER FUNCTIONS FOR WORDS ##########################################

	def segment_page_into_words(self):
		self.find_words(20,self.cols//2)
		self.store_words(0)
		no_words = len(os.listdir('./words'))		
		self.find_words(self.cols//2,self.cols)
		self.store_words(no_words)		
#############################################################################################
class letter_finder:
	def __init__(self,img):
		self.img = cv2.imread(img)
		self.img = cv2.resize(self.img,(0,0),fx=10,fy=5)
		avg = np.average(self.img)
		med = np.median(self.img)
		self.b_img = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
		thr_val = (avg) - 40
		(t,thr_img) = cv2.threshold(self.b_img,thr_val,255,cv2.THRESH_BINARY)
		self.thr_img = thr_img 
		self.rows = self.img.shape[0]
		self.cols = self.img.shape[1]

	def find_line(self):
		count_matrix = []
		for y in range(0,self.thr_img.shape[0]-1):
			count = 0
			for x in range(0,self.thr_img.shape[1]-1):
				if self.thr_img[y][x] == 0:
					count += 1
			count_matrix.append(count)
		for i in range(len(count_matrix)-2,0,-1):
			if count_matrix[i] > int(self.cols//5) :
				bottom_line = i
				break 
		return (count_matrix,bottom_line)

	def remove_line(self,count_matrix):
		margin = 11
		y_line = count_matrix[0].index(max(count_matrix[0]))
		upper_img = self.thr_img[0:(y_line - margin),0:self.cols]
		lower_img = self.thr_img[(y_line + margin):count_matrix[1],0:self.cols]
		
		final_image = np.concatenate((upper_img,lower_img),axis=0)
		#print('image has been formed without line')
		self.final_image = final_image

	def show_letters(self):
		for i in range(0,len(self.letter_matrix)-2):
			cv2.rectangle(self.img,(self.letter_matrix[i],0),(self.letter_matrix[i+1],self.cols),0,4)
		#print('letters are drawn')		

	def count_region(self,count_matrix,pos,r):
		count = sum(count_matrix[pos-r:pos+r])
		return count

	def find_letters(self,x1,y1,x2,y2):
		count_matrix = []
		letter_matrix = []
		letter_matrix.append(x1 + 10)
		for x in range(x1,x2):
			count = 0
			for y in range(y1,y2):
				if self.final_image[y][x] == 0:
					count += 1	
			count_matrix.append(count)
		#print(count_matrix)
		x = x1 + 80
		while x < len(count_matrix)-2:
			if self.count_region(count_matrix,x,3) < 2:
				if (x + x1) not in letter_matrix:
					letter_matrix.append(x + x1 + 10)
					x += 40
			x += 1
		#to correct errors like gha, sha, na
		#print('len',len(letter_matrix))
		for first,second in zip(letter_matrix,letter_matrix[1:]):
			if second - first < 65:
				letter_matrix.remove(first)
		#print('letters have been found')
		#print(letter_matrix)
		self.letter_matrix = letter_matrix
		self.no_words = len(letter_matrix)-1
		self.count_matrix = count_matrix

	def show_letters(self):#draws boxes around letters
		for i in range(0,len(self.letter_matrix)-1):
			cv2.rectangle(self.img,(self.letter_matrix[i],0),(self.letter_matrix[i+1],self.rows),0,1)
		#print('letters are drawn')	

	def resize_image(self,x,y):
		self.img = cv2.resize(self.img,(0,0),fx=x,fy=y)

	def show_image(self):
		cv2.imshow('letters',self.img)
		cv2.waitKey(0)

	def show_cropped_image(self):
		cv2.imshow('letters',self.final_image)
		cv2.waitKey(0)

	def plot_intensity(self):
		x = []
		for i in range(len(self.count_matrix)):
			x.append(i)
		
		plt.plot(x,self.count_matrix)
		plt.show()	
	
	def crop_letters(self,word_index):
		for x in range(0,len(self.letter_matrix)-1):
			letter = self.img[0:self.rows , self.letter_matrix[x]:self.letter_matrix[x+1]]
			letter = cv2.resize(letter,(0,0),fx=0.2,fy=0.2)
			cv2.imwrite('letters/' +str(word_index) + str(x)+'.png',letter)
		
		#print('letters have been stored...')	

	def store_cropped_letters(self,word_index):
		y = self.find_line()
		self.remove_line(y)
		self.find_letters(0,0,self.cols,self.final_image.shape[0])
		self.crop_letters(word_index)
		#self.show_letters()
		#self.show_image()
##################################test functions below###########################

#img = 'words/25.png'
#im = cv2.imread(img,0)
#im = cv2.resize(im,(0,0),fx=5,fy=5)
#cv2.imshow('t',im)
#cv2.waitKey()
#image = letter_finder(img)
#image.store_cropped_letters(0)
#y = image.find_line()
#image.remove_line(y)
#image.find_letters(0,0,image.cols,image.final_image.shape[0])
#image.show_letters()
#image.show_cropped_image()
#image.plot_intensity()
#image.crop_letters()
#image.show_cropped_image()
#img = './page/test' 
#image = word_finder(img)
#image.segment_page_into_words()
#image.store_cropped_letters(0#)

