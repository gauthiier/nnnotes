#output dir
OUT := ./

#csl - http://editor.citationstyles.org/
CSL :=

#bibliography file
BIB :=

#pdf
PDF := $(patsubst %.mmd,$(OUT)%.pdf,$(wildcard *.mmd))

$(OUT)%.pdf : %.mmd
	pandoc $< -o $@

#html
HTML := $(patsubst %.mmd,$(OUT)%.html,$(wildcard *.mmd))

$(OUT)%.html : %.mmd
	pandoc $< -s -t html5 --template=p/nnnote-template.html5 --filter pandoc-citeproc --csl $(CSL) --bibliography $(BIB) -o $@

all : dir $(HTML) index

index :
	parse.py < $(wildcard *.mmd)
                        
clean :
	rm -f $(HTML)
	rm -f $(PDF)

neat:
	rm *.bak

rebuild : clean all

dir : 
	mkdir -p $(OUT)
