import pytest
import temp_module



@pytest.fixture
def mock_interface(request,mocker):
    mock_a = request.param[0]
    mock_b = request.param[1]

    mocker.patch("temp_module.process.get_a", return_value=mock_a)
    mocker.patch("temp_module.process.get_b", return_value=mock_b)

  


    
@pytest.fixture
def expected(request):
    return request.param

# 用indirect之后, 这里所有的就好像都得是fixture注册的函数了. 所以封装了个expected
@pytest.mark.parametrize('mock_interface, expected',
                         [(('jack', 'abcdefgh'),'jackabcdefgh'),
                          (('tom', 'a123456a') , 'toma123456a')], indirect=True)
def test_process(mock_interface, expected):
    a =  temp_module.process.process_a()
    b =  temp_module.process.process_b()
    res =  f"{a}{b}"
    assert res == expected

