def test_blackbox_failure(blackbox):
    blackbox.log("user", "alice")
    blackbox.step("start")
    blackbox.attach("note.txt", "hello")
    assert 1 == 2
