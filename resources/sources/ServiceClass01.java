package sample

import com.example.mybatisdemo.mapper.SampleMapper02;

@Service
class Service01 extends ServieBase {

    private SampleMapper02 sampleDao;

    public void doService() {
        List<> records = sampleDao.subQuery01();
    }
}