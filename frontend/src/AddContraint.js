import {Center, Flex, Grid, Divider, Text, InputGroup, Input, InputRightAddon} from '@chakra-ui/react';
import {Button} from '@chakra-ui/react';
import {useState} from 'react';
import {Box} from '@chakra-ui/react';
import {AddIcon} from '@chakra-ui/icons';
import lodash from 'lodash';

const AddContraint = () => {
    const [buildingsList, setBuildingsList] = useState([]);
    const [buildingName, setBuildingName] = useState('');
    const [buildingSize, setBuildingSize] = useState();
    const [buildingTemp, setBuildingTemp] = useState();

    const addBuilding = () => {
        if (!lodash.isNil(buildingName)
            && !lodash.isNil(buildingSize)
            && !lodash.isNil(buildingTemp)
        ) {
            let building = {
                name: buildingName,
                size: buildingSize,
                temp: buildingTemp
            }
            setBuildingsList([...buildingsList, building]);
        }
    }

    const handleChangingBuildingName = (event) => {
        setBuildingName(event.target.value)
    }

    const handleChangingBuildingSize = (event) => {
        setBuildingSize(event.target.value)
    }

    const handleChangingBuildingTemp = (event) => {
        setBuildingTemp(event.target.value)
    }

    return (
        <Flex direction={'column'}>
            <Center w={'100%'} height={'5vh'}>
                <Text fontSize={'3xl'}>Add Constraint</Text>
            </Center>
            <Divider size={'100px'}/>
            <Text pt={'20px'} fontSize={'2xl'}>1. Add Buildings</Text>
            <Flex pt={'20px'}>
                <Grid w={'80%'} templateColumns={'30% 30% 30%'} gap={6}>
                    <InputGroup>
                        <Input placeholder={'Name'}
                               value={buildingName} onChange={handleChangingBuildingName}/>
                    </InputGroup>
                    <InputGroup>
                        <Input type={'number'} placeholder={'Size'}
                               value={buildingSize} onChange={handleChangingBuildingSize}/>
                        <InputRightAddon children={'m2'}/>
                    </InputGroup>
                    <InputGroup>
                        <Input type={'number'} placeholder={'Temperature'}
                               value={buildingTemp} onChange={handleChangingBuildingTemp}/>
                        <InputRightAddon children={'Celcius'}/>
                    </InputGroup>
                </Grid>
                <Flex w={'20%'}>
                    <Button w={'90%'} colorScheme={'green'} onClick={addBuilding}><AddIcon/></Button>
                </Flex>
            </Flex>
            <Box w={'100%'} pt={'30px'} pl={'17px'}>
                <Text fontSize={'lg'}>Number of buildings: {buildingsList.length}</Text>
                <Flex justifyItems={'space-between'} pt={'10px'} pl={'20px'}>
                    <Text fontSize={'md'} w={'30%'}>Name</Text>
                    <Text fontSize={'md'} w={'30%'} pl={'5px'}>Size</Text>
                    <Text fontSize={'md'} w={'30%'} pl={'5px'}>Temperature</Text>
                </Flex>
                {
                    buildingsList.map((building, index) => {
                        return (
                            <Flex pt={'7px'} key={'building-' + index} pl={'20px'}>
                                <Text w={'30%'} fontSize={'md'}>{building.name}</Text>
                                <Text w={'30%'} pl={'5px'} fontSize={'md'}>{building.size}</Text>
                                <Text w={'30%'} pl={'5px'} fontSize={'md'}>{building.temp}</Text>
                            </Flex>
                        );
                    })
                }
            </Box>
        </Flex>
    );
}

export default AddContraint