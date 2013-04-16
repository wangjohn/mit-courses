MIN_LECTURE = 1
MAX_LECTURE = 17
OUTPUT_LECTURE_NAME = 'lectures1-17.tex'

def compile_lectures(output_lecture_name)
  all_contents = []
  MIN_LECTURE.upto(MAX_LECTURE) do |lecture_number|
    lecture_name = "lecture#{lecture_number}.tex"
    contents = read_lecture(lecture_name)

    all_contents << pagebreak(lecture_number)
    all_contents << contents
  end

  output = all_contents.join("\n")

  File.open(output_lecture_name, 'w') do |file|
    file.write(output)
  end
end

def pagebreak(lecture_number)
  "\\newpage\n\\Large{Lecture #{lecture_number}}"
end

def read_lecture(lecture_name)
  File.open(lecture_name) do |file|
    scan_and_parse_contents(file.read)
  end
end

def scan_and_parse_contents(contents)
  actual_content = contents.scan(/\\begin{document}(.*)\\end{document}/m)
  actual_content[0]
end

compile_lectures(OUTPUT_LECTURE_NAME)
