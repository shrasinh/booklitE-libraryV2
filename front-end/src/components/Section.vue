<template>

    <h1>Sections</h1>
    {%if not sections%}
    <p class="text-muted">
      No sections are currently present.</p>
    <br>
    {%else%}
    {%set present=namespace(iterate=0)%}
    {%for section in sections%}
    {%if section.book%}
    {%set present.iterate=1%}
    <div class="row">
      <div class="row justify-content-between">
        <div class="col-3">
          <h3 style="font-family:Times New Roman" data-bs-toggle="popover" data-bs-placement="right"
            data-bs-title="Description" data-bs-custom-class="custom-popover"
            data-bs-content="{%if section['description'] %}{{section['description']}}{%else%}No description.{%endif%}">
            <strong>{{section.name}}</strong>
          </h3>
        </div>
        <div class="col-3 text-muted">Date created:{{section.date_created}}</div>
      </div>
      <hr>
      <div class="row">
        {%for book in section.book|reverse%}
        <div class="col-2">
          <div class="row"><img src="/static/thumbnail/book.thumbnail" class="img-fluid img-thumbnail"></div>
          <div class="row"><a href="/book/book.id">{{book.name}}</a></div>
          <div class="row"><span>Author: {{book.author}}</span></div>
          <div class="row"><span> Language: {{book.language}}</span></div>
          <div class="row"><span> Rating:{%if book.id in rating%} {{rating.book.id}} {%else%} No rating
              yet.{%endif%}</span></div>
        </div>
        <div class="col-1"></div>
        {%endfor%}
      </div>
    </div>
    <br>
    {%endif%}
    {%endfor%}
    {%if not present.iterate%}<p class="text-muted">
      No sections are currently present.</p>{%endif%}
    {%endif%}
  </template>