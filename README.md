# Запуск
1. Устанавливаем Docker
2. Клонируем репозиторий
> git clone https://github.com/WalderSasytZ/diploma_tests.git
3. Из директории diploma_tests выполняем команду ниже
> docker-compose up --build
4. Остановка
> docker-compose down -v

# Данные
После завершения работы сервис message_generator отправит сообщение в лог. После этого нужно выполнить SQL-запрос ниже к БД
```sql
-- Добавляем индексы в конце чтобы запрос отработал за пару секунд, а не 10 минут 
CREATE INDEX idx_results_sent ON results(sent);
CREATE INDEX idx_results_user_time ON results(user_id, sent);
CREATE INDEX idx_results_algorithm ON results(algorithm);

 SELECT algorithm                                              AS alg,
        AVG(delta)                                             AS avg_delta,
        SQRT(AVG(delta^2) - AVG(delta)^2)                      AS avg_deviation,
	      1.0 * COUNT(*) FILTER (WHERE delta > 5 )    / COUNT(*) AS delta_5s,
	      1.0 * COUNT(*) FILTER (WHERE delta > 10)    / COUNT(*) AS delta_10s,
	      1.0 * COUNT(*) FILTER (WHERE delta > 15)    / COUNT(*) AS delta_15s,
	      1.0 * COUNT(*) FILTER (WHERE delta > 20)    / COUNT(*) AS delta_20s,
	      1.0 * COUNT(*) FILTER (WHERE delta > 25)    / COUNT(*) AS delta_25s,
	      1.0 * COUNT(*) FILTER (WHERE delta > 30)    / COUNT(*) AS delta_30s,
	      1.0 * COUNT(*) FILTER (WHERE api_violation) / COUNT(*) AS violation
   FROM (
         SELECT algorithm,
  		          EXTRACT(EPOCH FROM sent - arrived) AS delta,
        		    (
        			      (
                		    SELECT COUNT(*) 
                          FROM results r2 
                         WHERE r2.sent BETWEEN r.sent - INTERVAL '1 second' AND r.sent
                           AND r2.algorithm = r.algorithm
        		        ) > 30
        		        OR 
        		        (
            			      SELECT COUNT(*) 
                          FROM results r3 
                         WHERE r3.sent BETWEEN r.sent - INTERVAL '60 second' AND r.sent
                           AND r3.user_id = r.user_id
                           AND r3.algorithm = r.algorithm
        		        ) > 20
        		    ) AS api_violation
           FROM results r
       ) b
 GROUP BY algorithm
```
