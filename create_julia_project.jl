#!/usr/bin/env julia

if length(ARGS) == 1
  println("Create $(ARGS[1]) project")
  create_template()
  my_template(ARGS[1])
else
  println("Use create_julia_project.jl ProjectName")
end
