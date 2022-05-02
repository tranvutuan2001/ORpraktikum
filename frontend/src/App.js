import {Box, ChakraProvider} from '@chakra-ui/react'
import {Center} from '@chakra-ui/react';
import {Grid} from '@chakra-ui/react';
import {GridItem} from '@chakra-ui/react';
import AddContraint from './AddContraint';
import Result from './Result';

function App() {
    return (
        <ChakraProvider>
            <Center bg={'#F7F7E8'}>
                <Grid templateColumns={'70% 30%'} w={'70%'} h={'100vh'} gap={2}
                      borderLeft={'1px solid #BABAB1'} borderRight={'1px solid #BABAB1'}>
                    <GridItem pl={'10px'} pr={'10px'}>
                        <AddContraint/>
                    </GridItem>
                    <GridItem borderLeft={'1px solid #BABAB1'}>
                        <Result/>
                    </GridItem>
                </Grid>
            </Center>
        </ChakraProvider>
    )
}

export default App;
