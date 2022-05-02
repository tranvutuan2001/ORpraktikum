import {Button, ChakraProvider, Flex} from '@chakra-ui/react'
import {Center} from '@chakra-ui/react';
import {Box} from '@chakra-ui/react';
import AddConstraint from './AddConstraint';
import Result from './Result';

function App() {
    return (
        <ChakraProvider>
            <Center bg={'#F7F7E8'}>
                <Flex w={'70%'} minH={'100vh'} borderLeft={'1px solid #BABAB1'} borderRight={'1px solid #BABAB1'}>
                    <Box w={'70%'} position={'relative'}>
                        <Box p={'10px'}>
                            <AddConstraint/>
                        </Box>
                        <Flex minH={'5vh'} w={'100%'}
                              justifyContent={'space-between'} position={'absolute'} bottom={0} p={'10px'}>
                            <Button bg={'#F01735'} color={'white'}>Reset</Button>
                            <Button bg={'#18AAEE'} color={'white'}>Calculate</Button>
                        </Flex>
                    </Box>
                    <Box w={'30%'} borderLeft={'1px solid #BABAB1'}>
                        <Result/>
                    </Box>
                </Flex>
            </Center>
        </ChakraProvider>
    )
}

export default App;
