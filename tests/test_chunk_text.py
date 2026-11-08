from app.rag import chunk_text

def test_chunk_text():
   actual = chunk_text("Hours---Guests")
   assert actual == ["Hours", "Guests"]

def test_chunk_text_multiple_sections():
   actual = chunk_text("Hours---Guests---Membership")
   assert actual == ["Hours", "Guests", "Membership"]

def test_chunk_text_no_separator():
   actual = chunk_text("Membership Hours")
   assert actual == ["Membership Hours"]

def test_chunk_text_no_empty_sections():
   actual = chunk_text("Hours------Guests")
   assert actual == ["Hours", "Guests"]

def test_chunk_text_whitespace_sections():
   actual = chunk_text("Hours---   ---Guests")
   assert actual == ["Hours", "Guests"]