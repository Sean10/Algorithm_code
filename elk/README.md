使用[spujadas/elk\-docker: Elasticsearch, Logstash, Kibana \(ELK\) Docker image](https://github.com/spujadas/elk-docker).




docker run --name filebeat  --user=root -v /Users/sean10/Code/ceph/ceph-14.2.9/src/out:/var/log/ceph -v /Users/sean10/Code/Algorithm_code/elk/logstash-beats.crt:/etc/certs/logstash-beats.crt -v /Users/sean10/Code/Algorithm_code/elk/filebeat.yml:/usr/share/filebeat/filebeat.yml -v /Users/sean10/Code/Algorithm_code/elk/hosts:/etc/hosts elastic/filebeat:7.10.1

暂时指定网络