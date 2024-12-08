#!/bin/bash

# Массив сервисов
services=("courses_service" "frontend" "tasks_service" "users_service")

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Запуск тестов для всех микросервисов..."

# Счетчики для статистики
total_services=0
successful_services=0
failed_services=0

for service in "${services[@]}"
do
    echo -e "\n${GREEN}=== Запуск тестов для $service ===${NC}"
    
    if [ ! -d "$service" ]; then
        echo -e "${YELLOW}Сервис $service не найден, пропускаем...${NC}"
        continue
    fi
    
    total_services=$((total_services + 1))
    cd $service
    ./run_tests.sh
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Тесты для $service прошли успешно${NC}"
        successful_services=$((successful_services + 1))
    else
        echo -e "${RED}✗ Тесты для $service завершились с ошибкой${NC}"
        failed_services=$((failed_services + 1))
    fi
    
    cd ..
done

echo -e "\n=== Итоговый результат ==="
echo -e "Всего сервисов проверено: ${total_services}"
echo -e "${GREEN}Успешно: ${successful_services}${NC}"
if [ $failed_services -gt 0 ]; then
    echo -e "${RED}С ошибками: ${failed_services}${NC}"
fi

if [ $failed_services -eq 0 ]; then
    echo -e "\n${GREEN}✓ Все тесты прошли успешно${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Обнаружены ошибки в ${failed_services} сервисах${NC}"
    exit 1
fi